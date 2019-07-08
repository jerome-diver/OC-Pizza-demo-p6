/*  Create types enum for:
  user.role           (name: role)
  contact.type        (name: contact_type)
  *.unit              (name: unity)
  order.status        (name: order_status)
  order_detail.status (name: pizza_status)
  *.size_pizza        (name: pizza_size) */
CREATE TYPE public.role AS ENUM
    ('Client', 'Manager', 'Pizzaiolo', 'Livreur', 'Comptable');
ALTER TYPE public.role OWNER TO "oc-pizza";
COMMENT ON TYPE public.role
    IS 'un utilisateur a un role qui lui donnera accès à des droits et des accès en fonction de ses droits.';
CREATE TYPE public.contact_type AS ENUM
    ('email', 'mobile', 'fixe', 'skype', 'whatsapp');
ALTER TYPE public.contact_type OWNER TO "oc-pizza";
COMMENT ON TYPE public.contact_type
    IS 'Type de donné de contact: [email, mobile, fixe, whatsapp, skype]';
CREATE TYPE public.unity AS ENUM
    ('kg', 'grammes', 'litre', 'cl', 'unité', 'bars', 'psi');
ALTER TYPE public.unity OWNER TO "oc-pizza";
COMMENT ON TYPE public.unity
    IS 'Unités de valeurs.';
CREATE TYPE public.order_status AS ENUM
    ('en attente', 'en préparation', 'prête', 'livraison en cours', 'livrée');
ALTER TYPE public.order_status OWNER TO "oc-pizza";
COMMENT ON TYPE public.order_status
    IS 'Status de la commande';
CREATE TYPE public.pizza_status AS ENUM
    ('en attente', 'en préparation', 'dans le four', 'prête');
ALTER TYPE public.pizza_status OWNER TO "oc-pizza";
COMMENT ON TYPE public.pizza_status
    IS 'Status de la pizza d''une commande en cours';
CREATE TYPE public.pizza_size AS ENUM
    ('individuelle', 'gourmande', 'familliale');
ALTER TYPE public.pizza_size OWNER TO "oc-pizza";
COMMENT ON TYPE public.pizza_size
    IS 'La taille de la pizza';
/*  Create table user */
CREATE TABLE IF NOT EXISTS public."user"
(
    id bigserial,
    nom character varying NOT NULL,
    prenom character varying NOT NULL,
    username character varying NOT NULL,
    thumb bytea,
    photo_url character varying,
    salt character varying NOT NULL,
    password character varying NOT NULL,
    enabled boolean NOT NULL DEFAULT False,
    role role NOT NULL DEFAULT 'Client'::role,
    PRIMARY KEY (id),
    CONSTRAINT unique_username UNIQUE (username)
,
    CONSTRAINT unique_photo_url UNIQUE (photo_url)
,
    CONSTRAINT username_bigger_than_7_chars CHECK (char_length(username) >= 8)
) WITH ( OIDS = FALSE );
ALTER TABLE public."user" OWNER to "oc-pizza";
COMMENT ON TABLE public."user"
    IS 'Utilisateurs enregistrés (clients, employés et gérants)';
COMMENT ON COLUMN public."user".nom
    IS 'Nom de famille';
COMMENT ON COLUMN public."user".username
    IS 'Nom de login (unique et plus de 8 caractères)';
COMMENT ON COLUMN public."user".thumb
    IS 'photo compressé (image identique à la photo stockée dans le répertoire des photos, mais de taille inférieur et de poids maximum de 8 Ko)';
COMMENT ON COLUMN public."user".photo_url
    IS 'le nom de la photo qui sear stocké dans le répertoire des photos
(unique)';
COMMENT ON COLUMN public."user".password
    IS 'mot de passe "hashé" et ducis (salt)';
COMMENT ON COLUMN public."user".enabled
    IS 'L''utilisateur peut-il se connecter ? (il le peut quand il a répondu à son email de confirmation)
Par défaut, il ne peut pas (False).';
COMMENT ON CONSTRAINT unique_username ON public."user"
    IS 'username est unique';
COMMENT ON CONSTRAINT unique_photo_url ON public."user"
    IS 'le nom de la photo doit être unique (c''est le système du site qui génère le nom et le stock)';
COMMENT ON CONSTRAINT username_bigger_than_7_chars ON public."user"
    IS 'Le nom d''utilisateur doit avoir au moins 8 caractères';
/*  Create table address */
CREATE TABLE IF NOT EXISTS public.address
(
    id bigserial,
    rue_1 character varying COLLATE pg_catalog."default",
    rue_2 character varying COLLATE pg_catalog."default",
    cp character varying COLLATE pg_catalog."default",
    ville character varying COLLATE pg_catalog."default",
    batiment character varying COLLATE pg_catalog."default",
    porte character varying COLLATE pg_catalog."default",
    code character varying COLLATE pg_catalog."default",
    autre character varying COLLATE pg_catalog."default",
    CONSTRAINT address_pkey PRIMARY KEY (id)
) WITH ( OIDS = FALSE )
TABLESPACE pg_default;
ALTER TABLE public.address OWNER to "oc-pizza";
COMMENT ON TABLE public.address
    IS 'Liste d''adresses.';
CREATE TABLE public.contact
(
    id bigserial,
    type contact_type NOT NULL,
    data character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT contact_pkey PRIMARY KEY (id),
    CONSTRAINT contact_uniq_data UNIQUE (data)
) WITH ( OIDS = FALSE )
TABLESPACE pg_default;
ALTER TABLE public.contact OWNER to "oc-pizza";
COMMENT ON TABLE public.contact
    IS 'Liste de contacts';
/* Create relational table user_addresses_contacts */
CREATE TABLE IF NOT EXISTS public.user_addresses_contacts
(
    user_id bigint NOT NULL,
    address_id bigint,
    contact_id bigint,
    CONSTRAINT unique_user_address_contact_ids UNIQUE (user_id, address_id, contact_id),
    CONSTRAINT user_adresses_contacts_to_user_id FOREIGN KEY (user_id)
        REFERENCES public."user" (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT user_adresses_contacts_to_address_id FOREIGN KEY (user_id)
        REFERENCES public.address (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT user_addresses_contacts_to_contact_id FOREIGN KEY (user_id)
        REFERENCES public.contact (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
) WITH ( OIDS = FALSE );
ALTER TABLE public.user_addresses_contacts OWNER to "oc-pizza";
COMMENT ON TABLE public.user_addresses_contacts
    IS 'table de relation plusieurs-plusieurs entre user, address et contact.';
COMMENT ON CONSTRAINT user_adresses_contacts_to_user_id ON public.user_addresses_contacts
    IS 'lien vers la table user';
COMMENT ON CONSTRAINT user_adresses_contacts_to_address_id ON public.user_addresses_contacts
    IS 'liens vers la table address';
/*  Create table provider */
CREATE TABLE IF NOT EXISTS public.provider
(
    id bigserial,
    nom character varying,
    address_id bigint,
    contact_id bigint,
    PRIMARY KEY (id),
    CONSTRAINT provider_contact_id FOREIGN KEY (contact_id)
        REFERENCES public.contact (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT provider_address_id FOREIGN KEY (address_id)
        REFERENCES public.address (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
) WITH ( OIDS = FALSE );
ALTER TABLE public.provider OWNER to "oc-pizza";
COMMENT ON TABLE public.provider
    IS 'Fournisseurs pour les produits';
COMMENT ON CONSTRAINT provider_contact_id ON public.provider
    IS 'Lien vers un moyen de contact';
COMMENT ON CONSTRAINT provider_address_id ON public.provider
    IS 'liens vers une adresse';
/*  Create table restaurant */
CREATE TABLE IF NOT EXISTS public.restaurant
(
    id bigserial,
    nom character varying NOT NULL,
    address_id bigint NOT NULL,
    contact_id bigint NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT restaurant_address_id FOREIGN KEY (address_id)
        REFERENCES public.address (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT reastaurant_contact_id FOREIGN KEY (contact_id)
        REFERENCES public.contact (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
) WITH ( OIDS = FALSE );
ALTER TABLE public.restaurant OWNER to "oc-pizza";
COMMENT ON TABLE public.restaurant
    IS 'Liste des sites de restauration de la chaine OC-Pizza';
COMMENT ON CONSTRAINT restaurant_address_id ON public.restaurant
    IS 'Lien vers une adresse';
COMMENT ON CONSTRAINT reastaurant_contact_id ON public.restaurant
    IS 'Lien vers un moyen de contact';
/*  Create table authentication_log */
CREATE TABLE IF NOT EXISTS public.authentication_log
(
    id bigserial,
    user_id bigint NOT NULL,
    date_time_login timestamp without time zone,
    date_time_logout timestamp without time zone,
    ip inet NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT authentication_log_user_id FOREIGN KEY (user_id)
        REFERENCES public."user" (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
) WITH ( OIDS = FALSE );
ALTER TABLE public.authentication_log
    OWNER to "oc-pizza";
COMMENT ON TABLE public.authentication_log
    IS 'Liste de traces de connections des utilisateurs loggés';
COMMENT ON CONSTRAINT authentication_log_user_id ON public.authentication_log
    IS 'Lien vers un utilisateur loggé';
/* Create table promotion */
CREATE TABLE IF NOT EXISTS public.promotion
(
    id bigserial,
    nom character varying NOT NULL,
    value integer NOT NULL,
    date_start date,
    date_end date,
    enabled boolean,
    PRIMARY KEY (id),
    CONSTRAINT promotion_value_ability CHECK (value <= 100 AND value >= 1) NOT VALID
) WITH ( OIDS = FALSE );
ALTER TABLE public.promotion OWNER to "oc-pizza";
COMMENT ON TABLE public.promotion
    IS 'Liste des promotions applicables';
COMMENT ON CONSTRAINT promotion_value_ability ON public.promotion
    IS 'La valeur de la promotion est un nombre entre 1 et 100 et représente un pourcentage';
/* Create table nutriment */
CREATE TABLE IF NOT EXISTS  public.nutriment
(
    id bigserial,
    nom character varying NOT NULL,
    provider_id bigint NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT nutriment_uniq_nom__provider_id UNIQUE (nom, provider_id),
    CONSTRAINT nutriment_provider_id FOREIGN KEY (provider_id)
        REFERENCES public.provider (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
) WITH ( OIDS = FALSE );
ALTER TABLE public.nutriment OWNER to "oc-pizza";
COMMENT ON TABLE public.nutriment
    IS 'Liste des produits de confection';
COMMENT ON CONSTRAINT nutriment_provider_id ON public.nutriment
    IS 'Liens vers le fournisseur du produit';
/*  Create table drink */
CREATE TABLE IF NOT EXISTS public.drink
(
    id bigserial,
    nom character varying NOT NULL,
    size character varying NOT NULL,
    pakaging character varying NOT NULL,
    provider_id bigint NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT drink_provider_id FOREIGN KEY (provider_id)
        REFERENCES public.provider (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
) WITH ( OIDS = FALSE );
ALTER TABLE public.drink OWNER to "oc-pizza";
COMMENT ON TABLE public.drink
    IS 'Liste des boissons';
COMMENT ON CONSTRAINT drink_provider_id ON public.drink
    IS 'Liens vers le fournisseur de la boisson';
/*  Create table stock */
CREATE TABLE IF NOT EXISTS public.stock
(
    id bigserial,
    restaurant_id bigint NOT NULL,
    nutriment_id bigint,
    drink_id bigint,
    quantity numeric(6,2) NOT NULL,
    unit unity NOT NULL,
    CONSTRAINT stock_pkey PRIMARY KEY (id),
    CONSTRAINT stock_has_uniq_drink_restaurant UNIQUE (restaurant_id, drink_id),
    CONSTRAINT stock_has_uniq_restaurant_nutriment UNIQUE (restaurant_id, nutriment_id),
    CONSTRAINT stock_to_drink_id FOREIGN KEY (drink_id)
        REFERENCES public.drink (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT stock_to_nutriment_id FOREIGN KEY (nutriment_id)
        REFERENCES public.nutriment (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT stock_to_restaurant_id FOREIGN KEY (restaurant_id)
        REFERENCES public.restaurant (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT stock_nutriment_xor_drink CHECK ((nutriment_id IS NULL) <> (drink_id IS NULL))
) WITH ( OIDS = FALSE )
TABLESPACE pg_default;
ALTER TABLE public.stock OWNER to "oc-pizza";
COMMENT ON TABLE public.stock
    IS 'Liste des produits en stock dans les restaurants.';
COMMENT ON CONSTRAINT stock_to_drink_id ON public.stock
    IS 'Lien vers les boissons';
COMMENT ON CONSTRAINT stock_to_restaurant_id ON public.stock
    IS 'Lien vers le restaurant concerné pas son stock';
COMMENT ON CONSTRAINT stock_nutriment_xor_drink ON public.stock
    IS 'Contraint d''avoir une entrée liée vers les aliments OU vers les boissons, mais JAMAIS les deux en même temps';
/*  Create table pizza */
CREATE TABLE IF NOT EXISTS public.pizza
(
    id bigserial,
    nom character varying COLLATE pg_catalog."default" NOT NULL,
    thumb bytea NOT NULL,
    photo_url character varying COLLATE pg_catalog."default" NOT NULL,
    description text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT pizza_pkey PRIMARY KEY (id),
    CONSTRAINT pizza_uniq_nom UNIQUE (nom),
    CONSTRAINT pizza_uniq_photo_url UNIQUE (photo_url)
) WITH ( OIDS = FALSE )
TABLESPACE pg_default;
ALTER TABLE public.pizza OWNER to "oc-pizza";
COMMENT ON TABLE public.pizza
    IS 'Liste des pizzas';
COMMENT ON CONSTRAINT pizza_uniq_nom ON public.pizza
    IS 'le nom de la pizza est unique';
COMMENT ON CONSTRAINT pizza_uniq_photo_url ON public.pizza
    IS 'le nom du fichier de la photo est unique (il est généré par le système)'

/*  Create table recipe */
CREATE TABLE IF NOT EXISTS public.recipe
(
    pizza_id bigint NOT NULL,
    nutriment_id bigint NOT NULL,
    quantity bigint NOT NULL,
    unit unity NOT NULL,
    CONSTRAINT recipe_uniq_pizza_nutriment UNIQUE (pizza_id, nutriment_id),
    CONSTRAINT recipe_pizza_id FOREIGN KEY (pizza_id)
        REFERENCES public.pizza (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT recipe_nutriment_id FOREIGN KEY (nutriment_id)
        REFERENCES public.nutriment (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
) WITH ( OIDS = FALSE );
ALTER TABLE public.recipe OWNER to "oc-pizza";
COMMENT ON TABLE public.recipe
    IS 'Les recettes des pizzas: une recette est constitué de plusieurs aliments quantifiables. De facto c''est une table relationelle many-to-many avec en plus des quantités et une unité de mesure liée à l''unité.';
COMMENT ON CONSTRAINT recipe_uniq_pizza_nutriment ON public.recipe
    IS 'les liens entre une pizza et ses aliment sont uniques';
COMMENT ON CONSTRAINT recipe_pizza_id ON public.recipe
    IS 'Lien vers la pizza';
COMMENT ON CONSTRAINT recipe_nutriment_id ON public.recipe
    IS 'Lien vers l''aliment';
/*  Create table order */
CREATE TABLE IF NOT EXISTS public."order"
(
    id bigserial,
    restaurant_id bigint NOT NULL,
    user_id bigint NOT NULL,
    address_id bigint NOT NULL,
    promotion_id bigint,
    date timestamp with time zone DEFAULT now(),
    status order_status NOT NULL DEFAULT 'en attente'::order_status,
    paid boolean NOT NULL DEFAULT false,
    CONSTRAINT order_pkey PRIMARY KEY (id),
    CONSTRAINT order_address_id FOREIGN KEY (address_id)
        REFERENCES public.address (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT order_promotion_id FOREIGN KEY (promotion_id)
        REFERENCES public.promotion (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT order_restaurant_id FOREIGN KEY (restaurant_id)
        REFERENCES public.restaurant (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT order_user_id FOREIGN KEY (user_id)
        REFERENCES public."user" (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
) WITH ( OIDS = FALSE )
TABLESPACE pg_default;
ALTER TABLE public."order" OWNER to "oc-pizza";
COMMENT ON TABLE public."order"
    IS 'Liste des commandes';
COMMENT ON CONSTRAINT order_address_id ON public."order"
    IS 'Lien vers l''adresse de livraison';
COMMENT ON CONSTRAINT order_promotion_id ON public."order"
    IS 'Lien éventuel vers la promotion généralee sur toute la commande';
COMMENT ON CONSTRAINT order_restaurant_id ON public."order"
    IS 'Lien vers le resaaurant';
COMMENT ON CONSTRAINT order_user_id ON public."order"
    IS 'Lien vers le client';
/*  Create table order_detail */
CREATE TABLE IF NOT EXISTS public.order_detail
(
    order_id bigint NOT NULL,
    pizza_id bigint,
    drink_id bigint,
    option_id bigint NOT NULL,
    promotion_id bigint NOT NULL,
    status pizza_status NOT NULL DEFAULT 'en attente'::pizza_status,
    size pizza_size NOT NULL DEFAULT 'individuelle'::pizza_size,
    quantity smallint NOT NULL DEFAULT 1,
    CONSTRAINT order_detail_option_id FOREIGN KEY (option_id)
        REFERENCES public.option (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
    CONSTRAINT order_detail_drink_id FOREIGN KEY (drink_id)
        REFERENCES public.drink (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT order_detail_order_id FOREIGN KEY (order_id)
        REFERENCES public."order" (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT order_detail_pizza_id FOREIGN KEY (pizza_id)
        REFERENCES public.pizza (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT order_details_promotion_id FOREIGN KEY (promotion_id)
        REFERENCES public.promotion (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT order_detail_drink_xor_pizza CHECK ((pizza_id IS NULL) <> (drink_id IS NULL)) NOT VALID
) WITH ( OIDS = FALSE )
TABLESPACE pg_default;
ALTER TABLE public.order_detail OWNER to "oc-pizza";
COMMENT ON TABLE public.order_detail
    IS 'Details d''une commande (chaque pizza concerné et son status, sa taille, son prix). Il n''y a pas de quantité parce que chaque pizza peut avoir des options supplémentaires.';
COMMENT ON CONSTRAINT order_detail_drink_id ON public.order_detail
    IS 'Lien vers la boisson';
COMMENT ON CONSTRAINT order_detail_order_id ON public.order_detail
    IS 'Lien vers la commande';
COMMENT ON CONSTRAINT order_detail_pizza_id ON public.order_detail
    IS 'Lien vers la pizza';
COMMENT ON CONSTRAINT order_details_promotion_id ON public.order_detail
    IS 'Lien vers la promotion éventuelle';
COMMENT ON CONSTRAINT order_detail_drink_xor_pizza ON public.order_detail
    IS 'Le détail de commande concerne une pizza OU une boisson.';
/*  Create table option */
CREATE TABLE IF NOT EXISTS public.option
(
    id bigserial,
    nutriment_id bigint NOT NULL,
    nom character varying NOT NULL,
    description text COLLATE pg_catalog."default" NOT NULL,
    quantity integer NOT NULL,
    unit unity NOT NULL,
    CONSTRAINT option_pkey PRIMARY KEY (id),
    CONSTRAINT option_nutriment_id FOREIGN KEY (nutriment_id)
        REFERENCES public.nutriment (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
) WITH ( OIDS = FALSE )
TABLESPACE pg_default;
ALTER TABLE public.option OWNER to "oc-pizza";
COMMENT ON TABLE public.option
    IS 'Options possibles (extra sur pizza)';
COMMENT ON CONSTRAINT option_nutriment_id ON public.option
    IS 'Lien vers l''aliment';
/*  Create table menus_price */
CREATE TABLE IF NOT EXISTS public.price
(
    restaurant_id bigint NOT NULL,
    pizza_id bigint,
    drink_id bigint,
    option_id bigint,
    price numeric(4,2) NOT NULL,
    size_pizza pizza_size,
    CONSTRAINT price_drink_id FOREIGN KEY (drink_id)
        REFERENCES public.drink (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT price_option_id FOREIGN KEY (option_id)
        REFERENCES public.option (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT price_pizza_id FOREIGN KEY (pizza_id)
        REFERENCES public.pizza (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT price_pizza_xor_drink_xor_option CHECK (num_nonnulls(pizza_id, drink_id, option_id) = 1),
    CONSTRAINT price_pizza_id_and_pizza_size
      CHECK (pizza_id IS NULL AND size_pizza IS NULL OR pizza_id IS NOT NULL AND size_pizza IS NOT NULL) NOT VALID
) WITH ( OIDS = FALSE )
TABLESPACE pg_default;
ALTER TABLE public.menus_price OWNER to "oc-pizza";
COMMENT ON TABLE public.menus_price
    IS 'La liste des prix';
COMMENT ON CONSTRAINT price_drink_id ON public.menus_price
    IS 'Lien vers la boisson';
COMMENT ON CONSTRAINT price_option_id ON public.menus_price
    IS 'Lien vers l''option';
COMMENT ON CONSTRAINT price_pizza_id ON public.menus_price
    IS 'Lien ver la pizza';
COMMENT ON CONSTRAINT price_pizza_xor_drink_xor_option ON public.menus_price
    IS 'Au choix, le prix ne peut concerner que l''un ou l''autre: une pizza, une boisson ou une option';
COMMENT ON CONSTRAINT price_pizza_id_and_pizza_size ON public.menus_price
    IS 'Quand il y a un lien vers une pizza, il doit y avoir une dimension de pizza fourni pour obtenir un prix.';
/* Create table code_accounting */
CREATE TABLE IF NOT EXISTS public.code_accounting
(
    id bigserial,
    code integer NOT NULL,
    code_t character(6) NOT NULL,
    description character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT code_accounting_pkey PRIMARY KEY (id)
) WITH ( OIDS = FALSE )
TABLESPACE pg_default;
ALTER TABLE public.code_accounting OWNER to "oc-pizza";
COMMENT ON TABLE public.code_accounting
    IS 'Les codes comptables français.';
/*  Create table accounting */
CREATE TABLE IF NOT EXISTS public.accounting
(
    id bigserial,
    restaurant_id bigint NOT NULL,
    nutriment_id bigint,
    drink_id bigint,
    label character varying COLLATE pg_catalog."default",
    credit numeric(7,2),
    debit numeric(7,2),
    date_record date NOT NULL,
    date_declaration date,
    code_accounting__id bigint NOT NULL,
    order_id bigint,
    CONSTRAINT accounting_pkey PRIMARY KEY (id),
    CONSTRAINT accounting_code_accounting_id FOREIGN KEY (code_accounting__id)
        REFERENCES public.code_accounting (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT accounting_drink_id FOREIGN KEY (drink_id)
        REFERENCES public.drink (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT accounting_nutriment_id FOREIGN KEY (nutriment_id)
        REFERENCES public.nutriment (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT accounting_order_id FOREIGN KEY (order_id)
        REFERENCES public."order" (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT accounting_restaurant_id FOREIGN KEY (restaurant_id)
        REFERENCES public.restaurant (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT accounting_nutriment_xor_drink_xor_order
      CHECK (num_nonnulls(drink_id, nutriment_id, order_id) = 1)
) WITH ( OIDS = FALSE )
TABLESPACE pg_default;
ALTER TABLE public.accounting OWNER to "oc-pizza";
COMMENT ON TABLE public.accounting
    IS 'Lignes comptables pour les restaurants';
COMMENT ON CONSTRAINT accounting_code_accounting_id ON public.accounting
    IS 'Lien vers le code comptable';
COMMENT ON CONSTRAINT accounting_drink_id ON public.accounting
    IS 'Lien vers la boisson';
COMMENT ON CONSTRAINT accounting_nutriment_id ON public.accounting
    IS 'Lien vers le produit';
COMMENT ON CONSTRAINT accounting_order_id ON public.accounting
    IS 'Liens vers la commande encaissée';
COMMENT ON CONSTRAINT accounting_restaurant_id ON public.accounting
    IS 'Lien vers le restaurant';
COMMENT ON CONSTRAINT accounting_nutriment_xor_drink_xor_order ON public.accounting
    IS 'La ligne comptable doit concerné uniquement l''un ou l''autre: une commande encaissée, un produit acheté, une boisson achetée.';
/*  Create table delivery */
CREATE TABLE IF NOT EXISTS public.delivery
(
    id bigserial,
    order_id bigint NOT NULL,
    date date NOT NULL,
    time_record timestamp without time zone,
    time_start timestamp without time zone,
    time_end timestamp without time zone,
    time_send timestamp without time zone,
    time_delivered timestamp without time zone,
    CONSTRAINT delivery_pkey PRIMARY KEY (id),
    CONSTRAINT delivery_order_id FOREIGN KEY (order_id)
        REFERENCES public."order" (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
) WITH ( OIDS = FALSE )
TABLESPACE pg_default;
ALTER TABLE public.delivery OWNER to "oc-pizza";
COMMENT ON TABLE public.delivery
    IS 'La liste des livraisons';
COMMENT ON CONSTRAINT delivery_order_id ON public.delivery
    IS 'Lien vers la commande';
/*  Create table hand_over */
CREATE TABLE IF NOT EXISTS public.hand_over
(
    id bigserial,
    user_id bigint NOT NULL,
    start boolean NOT NULL DEFAULT false,
    date date,
    description text COLLATE pg_catalog."default",
    CONSTRAINT hand_over_pkey PRIMARY KEY (id),
    CONSTRAINT hand_over_user_id FOREIGN KEY (user_id)
        REFERENCES public."user" (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH ( OIDS = FALSE )
TABLESPACE pg_default;
ALTER TABLE public.hand_over OWNER to "oc-pizza";
COMMENT ON TABLE public.hand_over
    IS 'Liste de "hand_over". Le "hand_over" est utilisé par les employés pour décrire leur prise de service et leur fin de service (cela permet une détection des problèmes su rle matériel ou le stock de fournitures ou tout autre problème de prise ou de fin de service.';
COMMENT ON COLUMN public.hand_over.start
    IS 'start décrit si c''est une prise de service ou non. Dans le cas ou state est False, c''est une fin de service.';
COMMENT ON CONSTRAINT hand_over_user_id ON public.hand_over
    IS 'Lien vers le client';
